import logging
from models import RawEvent, ProcessedFeature
from state import update_window_aggregate, update_count

logger = logging.getLogger(__name__)

async def process_features(stream, feature_table, count_table, processed_topic):
    """
    Process the stream of RawEvents.
    Updates rolling window features and global counts.
    Emits ProcessedFeatures to the output topic.
    """
    async for event in stream:
        try:
            # 1. Update Count (Feature B)
            # count_table[key] returns the value. modifying it updates state.
            # Tables in Faust are usually accessed like dicts.
            current_count = count_table[event.user_id] or 0
            new_count = update_count(current_count)
            count_table[event.user_id] = new_count
            
            # 2. Update Windowed Feature (Feature A)
            # Windowed tables are accessed with .current() or by iterating
            # Since we want "last N seconds", we rely on the windowed table configuration in main.py
            # feature_table[user_id] += event.amount will automatically bucketize if configured.
            feature_table[event.user_id] += event.amount
            
            # 3. Retrieve Aggregated Window Value
            # To get the sum over the window, we might need value() or similar.
            # feature_table[user_id] returns the current window value (sum).
            window_sum = feature_table[event.user_id].current()
            
            # 4. Construct Processed Feature
            output = ProcessedFeature(
                user_id=event.user_id,
                feature_a={"sum_10s": window_sum},  # Feature A
                feature_b=new_count,                # Feature B
                last_updated_timestamp=event.timestamp
            )
            
            # 5. Emit
            await processed_topic.send(value=output)
            
            if new_count % 100 == 0:
                logger.info(f"User {event.user_id} processed. Count: {new_count}, WindowSum: {window_sum}")
                
        except Exception as e:
            logger.error(f"Error processing event for user {event.user_id}: {e}", exc_info=True)
