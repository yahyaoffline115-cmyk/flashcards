def schedule(rating, interval, ease):
    """
    SM-2 spaced repetition.
    rating: 1=Again, 2=Hard, 3=Good, 4=Easy
    Returns (new_interval, new_ease)
    """
    if rating == 1:
        return 1, max(1.3, ease - 0.2)

    if rating == 2:
        ease = max(1.3, ease - 0.15)
        new_interval = max(1, round(interval * 1.2))
    elif rating == 3:
        new_interval = max(1, round(interval * ease))
    else:
        ease = ease + 0.15
        new_interval = max(1, round(interval * ease * 1.3))

    return new_interval, ease