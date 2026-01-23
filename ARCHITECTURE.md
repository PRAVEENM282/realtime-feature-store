# System Architecture

## Design Decisions

### Event-Driven Architecture
We utilized **Apache Kafka** as the central nervous system. This decouples the **Data Generator** (producers) from the **Feature Processors** (consumers), allowing for independent scaling and failure isolation.

### Stream Processing with Faust
We chose **Faust** for its pythonic approach to stream processing, seamless asyncio integration, and built-in support for:
- **Rolling Windows**: Managed via RocksDB for high-performant local state.
- **Table Abstractions**: Simplifies distributed state management (counts, aggregations).
- **Agent Model**: Clean separation of processing logic.

### Database Strategy
**PostgreSQL** serves as the persistent Feature Store. We use an **Upsert Pattern** (Idempotent Writes) to ensure that re-processing events (e.g., during recovery) does not corrupt the state. `db_writer_service` decouples the high-throughput Kafka stream from the potentially slower database writes, providing backpressure handling.

### API Layer
**FastAPI** provides a high-performance, async interface to the Feature Store. It connects via a connection pool to Postgres, ensuring low latency for inference requests.

### Frontend Layer
**Frontend Dashboard** provides a real-time visualization of the calculated features. It interacts with the API layer via REST to display live updates of user data.

## Scalability Strategy

- **Horizontal Scaling**:
  - **Kafka**: Partitioning topics allows multiple consumers.
  - **Faust**: Running multiple replicas of `faust_app` will automatically rebalance partitions and state.
  - **DB Writer**: Can scale stateless workers to handle higher write throughput.
  - **API**: Stateless, easy to scale behind a Load Balancer.

- **State Management**:
  - **RocksDB** (local to Faust workers) handles high-speed windowing without network overhead.
  - **Changelog Topics**: Faust backs up local state to Kafka, ensuring state recovery on pod restart/migration.

## Failure Handling

- **Kafka Downtime**: Services implement retry loops and buffering (via `aiokafka`).
- **Database Downtime**: The `db_writer_service` will fail to commit offsets if writes fail, ensuring no data loss. It will retry indefinitely until DB is back.
- **Service Crashes**: Docker Compose (and K8s in prod) handles restarts. State is recovered from RocksDB/Kafka.

## Production Deployment Path

1. **Container Orchestration**: Deploy to Kubernetes (EKS/GKE).
2. **Managed Services**: Replace containerized Kafka/Zookeeper/Postgres with managed equivalents (MSK, RDS).
3. **Security**:
   - Enable SSL/TLS for Kafka and DB connections.
   - Implement IAM authentication for RDS.
   - Use Vault for secrets management.

## Security Extension Plan

- **API Security**: Implement OAuth2 / JWT middleware in FastAPI.
- **Network Policy**: Restrict direct DB access to only `db_writer` and `fastapi_app`.
- **Encryption**: Enable encryption at rest for RocksDB and Postgres.
