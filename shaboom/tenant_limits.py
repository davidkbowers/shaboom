def tenant_limit_callback(tenant):
    """
    Define tenant-specific limits and settings.
    This function is called when a tenant is created or updated.
    """
    limits = {
        'max_users': 10,  # Default max users per tenant
        'max_storage': 1073741824,  # 1GB default storage limit in bytes
        'can_upload_videos': True,
        'video_quality': '720p',  # Default video quality
    }
    
    # Example: Set different limits based on tenant type or subscription
    if tenant.on_trial:
        limits.update({
            'max_users': 5,
            'max_storage': 536870912,  # 500MB for trial
            'can_upload_videos': True,
            'video_quality': '480p',
        })
    
    return limits
