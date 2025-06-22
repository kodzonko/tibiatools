import re
import pandas as pd

# Połączone wyrażenie regularne z trzema alternatywami:
pattern = re.compile(
    r"""
^(?P<time>\d{2}:\d{2}:\d{2})\s+
(?:
    # Damage event: target loses X hitpoints due to an attack by actor.
    (?P<target_d>[\w\s']+)\s+loses\s+(?P<points_d>\d+)\s+(?P<resource_d>hitpoints?)\s+due\s+to\s+an\s+attack\s+by\s+(?P<actor_d>[\w\s']+)\.
  |
    # Healing by another entity: target was healed by actor for X hitpoints.
    (?P<target_h>[\w\s']+)\s+was\s+healed\s+by\s+(?P<actor_h>[\w\s']+)\s+for\s+(?P<points_h>\d+)\s+(?P<resource_h>hitpoints?)\.
  |
    # Self-healing: actor healed himself/herself for X hitpoints.
    (?P<actor_sh>[\w\s']+)\s+healed\s+(?:himself|herself)\s+for\s+(?P<points_sh>\d+)\s+(?P<resource_sh>hitpoints?)\.
)
$
""",
    re.VERBOSE,
)

# Lista do przechowywania sparsowanych danych
data = []

# Wczytaj logi (upewnij się, że ścieżka do pliku jest poprawna)
with open(
    r"C:\Users\janwa\AppData\Local\Tibia\packages\Tibia\log\Server Log.txt", "r"
) as file:
    for line in file:
        line = line.strip()
        match = pattern.match(line)
        if match:
            # Domyślne wartości
            timestamp = match.group("time")
            actor = None
            points = None
            action = None
            target = None
            resource = None

            # Damage event
            if match.group("actor_d"):
                actor = match.group("actor_d")
                points = int(match.group("points_d"))
                action = "attack"
                target = match.group("target_d")
                resource = match.group("resource_d")
            # Healing by others
            elif match.group("actor_h"):
                actor = match.group("actor_h")
                points = int(match.group("points_h"))
                action = "heal"
                target = match.group("target_h")
                resource = match.group("resource_h")
            # Self-healing
            elif match.group("actor_sh"):
                actor = match.group("actor_sh")
                points = int(match.group("points_sh"))
                action = "self-heal"
                target = actor  # self-heal => target to ten sam aktor
                resource = match.group("resource_sh")

            data.append(
                {
                    "timestamp": timestamp,
                    "actor": actor,
                    "points": points,
                    "action": action,
                    "target": target,
                    "resource": resource,
                    "message": line,
                }
            )

# Stwórz DataFrame
df = pd.DataFrame(data)
print(df.head())
import qgrid

qgrid_widget = qgrid.show_grid(df, show_toolbar=True)
qgrid_widget
