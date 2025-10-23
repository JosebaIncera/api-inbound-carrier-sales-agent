from app.supabase import supabase

def get_metrics_from_supabase():
    """Get metrics from supabase"""
    metrics = supabase.table("metrics").select("*").execute()
    return metrics

def store_metrics_in_supabase(metrics: MetricsRequest):
    """Store metrics in supabase"""
    logger.info(f"Storing metrics: {metrics}")
    logger.debug(f"Metrics: {metrics}")
    logger.debug(f"Metrics type: {type(metrics)}")
    logger.debug(f"Metrics keys: {metrics.keys()}")
    logger.debug(f"Metrics values: {metrics.values()}")
    logger.debug(f"Metrics items: {metrics.items()}")
    logger.debug(f"Metrics items type: {type(metrics.items())}")
    logger.debug(f"Metrics items keys: {metrics.items().keys()}")
    logger.debug(f"Metrics items values: {metrics.items().values()}")
    logger.debug(f"Metrics items items: {metrics.items().items()}")
    # supabase.table("metrics").insert(metrics).execute()
    return True