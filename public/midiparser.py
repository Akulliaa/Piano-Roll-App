#!/usr/bin/env python3
"""
midiparser.py: Improved MIDI parser with accurate event timing using tempo mapping.
Extracts:
- Notes (with velocity, start/end time, channel, track)
- Tempo changes
- Time signature changes
- Key signature changes
- Pedal controls
- Program (instrument) changes
- Accurate playback schedule
"""
import mido
import json
import argparse

def parse_midi(file_path):
    mid = mido.MidiFile(file_path)
    ticks_per_beat = mid.ticks_per_beat

    # Build tempo map: list of (tick, tempo)
    tempo_events = [(0, 500000)]  # default tempo = 120 BPM

    raw_events = []  # (tick, msg, track)
    for i, track in enumerate(mid.tracks):
        tick = 0
        for msg in track:
            tick += msg.time
            raw_events.append((tick, msg, i))
            if msg.type == 'set_tempo':
                tempo_events.append((tick, msg.tempo))

    tempo_events.sort()
    raw_events.sort(key=lambda x: x[0])

    def tick_to_seconds(target_tick):
        seconds = 0.0
        last_tick = 0
        last_tempo = tempo_events[0][1]
        for t, tempo in tempo_events[1:]:
            if target_tick < t:
                break
            delta_ticks = t - last_tick
            seconds += mido.tick2second(delta_ticks, ticks_per_beat, last_tempo)
            last_tick = t
            last_tempo = tempo
        delta_ticks = target_tick - last_tick
        seconds += mido.tick2second(delta_ticks, ticks_per_beat, last_tempo)
        return seconds

    notes = []
    active_notes = {}
    pedals = {'sustain': [], 'expression': []}
    tempo_changes = []
    time_signatures = []
    key_signatures = []
    program_changes = []
    playback_schedule = []

    for tick, msg, track_idx in raw_events:
        time_sec = tick_to_seconds(tick)

        if msg.type == 'set_tempo':
            tempo_changes.append({
                'time': time_sec,
                'tempo': mido.tempo2bpm(msg.tempo)
            })

        elif msg.type == 'time_signature':
            time_signatures.append({
                'time': time_sec,
                'numerator': msg.numerator,
                'denominator': msg.denominator
            })

        elif msg.type == 'key_signature':
            key_signatures.append({
                'time': time_sec,
                'key': msg.key
            })

        elif msg.type == 'program_change':
            program_changes.append({
                'time': time_sec,
                'channel': msg.channel,
                'program': msg.program
            })

        elif msg.type == 'control_change':
            if msg.control == 64:
                pedals['sustain'].append({'time': time_sec, 'value': msg.value})
                playback_schedule.append({
                    'time': time_sec,
                    'type': 'pedal',
                    'value': msg.value
                })
            elif msg.control == 11:
                pedals['expression'].append({'time': time_sec, 'value': msg.value})

        elif msg.type == 'note_on' and msg.velocity > 0:
            key = (msg.channel, msg.note)
            active_notes[key] = {
                'note': msg.note,
                'start': time_sec,
                'velocity': msg.velocity,
                'channel': msg.channel,
                'track': track_idx
            }
            playback_schedule.append({
                'time': time_sec,
                'type': 'on',
                'note': msg.note,
                'velocity': msg.velocity
            })

        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            key = (msg.channel, msg.note)
            note_info = active_notes.pop(key, None)
            if note_info:
                notes.append({
                    'note': msg.note,
                    'start': note_info['start'],
                    'end': time_sec,
                    'velocity': note_info['velocity'],
                    'channel': note_info['channel'],
                    'track': note_info['track']
                })
            playback_schedule.append({
                'time': time_sec,
                'type': 'off',
                'note': msg.note,
                'velocity': 0
            })

    playback_schedule.sort(key=lambda x: x['time'])

    return {
        'ticks_per_beat': ticks_per_beat,
        'tempo_changes': tempo_changes,
        'time_signatures': time_signatures,
        'key_signatures': key_signatures,
        'program_changes': program_changes,
        'notes': notes,
        'pedals': pedals,
        'playback_schedule': playback_schedule
    }

def main():
    parser = argparse.ArgumentParser(description='Parse a MIDI file into JSON.')
    parser.add_argument('midi_file', help='Path to the MIDI file')
    parser.add_argument('-o', '--output', help='Path for output JSON file')
    args = parser.parse_args()

    data = parse_midi(args.midi_file)
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=2)
        print(f'JSON data saved to {args.output}')
    else:
        print(json.dumps(data, indent=2))

if __name__ == '__main__':
    main()