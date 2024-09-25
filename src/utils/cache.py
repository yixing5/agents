from core.config import config 
import hermes.backend.redis
cache = hermes.Hermes(
  hermes.backend.redis.Backend,
  ttl   = config.CACHE_TTL,
  host  = config.CACHE_HOST,
  port  = config.CACHE_PORT,
  db    = config.CACHE_DB,
)
# cache.clean()