"""Send one cabinet service input while the game is running."""
from pathlib import Path
import argparse,json,time
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('action',choices=['test','service','confirm','up','down'])
a=p.parse_args()
state={'test':{'bits':1<<15},'service':{'bits':1<<14},'confirm':{'buttons':[3]},'up':{'buttons':[9]},'down':{'buttons':[10]}}[a.action]
target=Path(__file__).resolve().parents[1]/'logs/test-input.json'
if not target.parent.exists():raise SystemExit('Start the game first')
try:
 target.write_text(json.dumps(state));time.sleep(.15)
 target.write_text('{}');time.sleep(.15)
finally:target.unlink(missing_ok=True)
