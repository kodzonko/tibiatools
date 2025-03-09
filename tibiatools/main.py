from datetime import datetime, timedelta

import click


@click.command()
@click.argument("charges", type=click.IntRange(1))
def exercise_weapon_burnout_time(charges: int):
    """Given the number of charges of an exercise weapon, calculate the time it will burn out."""
    current_time = datetime.now()
    time_delta = charges * 2
    future_time = current_time + timedelta(seconds=time_delta)

    click.echo(
        f"Exercise weapon will burn out at {future_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
