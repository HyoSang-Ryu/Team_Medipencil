"""Opt-in external STT smoke test using only newly synthesized non-clinical speech.

Requires the local demo at :8780, macOS say, and Homebrew ffmpeg.
No supplied EMR, recording, API key, or resident context is read by this script.
"""
import argparse
import asyncio
import json
import subprocess
import tempfile
import time
from pathlib import Path

import httpx
from websockets.asyncio.client import connect


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--send-synthetic-audio', action='store_true')
    if not parser.parse_args().send_synthetic_audio:
        parser.error('Explicit --send-synthetic-audio is required for external transmission')
    origin = 'http://127.0.0.1:8780'
    with httpx.Client(base_url=origin, headers={'Origin': origin}) as client:
        login = client.post('/api/v1/demo/session', json={'demo_actor_id': 'staff'})
        login.raise_for_status()
        client.headers['x-csrf-token'] = login.json()['data']['csrf_token']
        cookie = '; '.join(k + '=' + v for k, v in client.cookies.items())
        with tempfile.TemporaryDirectory(prefix='roundloop-synthetic-') as tmp:
            for language, voice, phrase in [
                ('ko', 'Eddy (한국어(한국))', '이것은 합성 음성 테스트입니다.'),
                ('en', 'Eddy (영어(미국))', 'This is a synthetic speech test.'),
                ('fi', 'Eddy (핀란드어(핀란드))', 'Tämä on synteettinen puhetesti.'),
            ]:
                root = Path(tmp)
                subprocess.run(['say', '-v', voice, '-o', str(root/'speech.aiff'), phrase], check=True, capture_output=True)
                subprocess.run(['/opt/homebrew/bin/ffmpeg', '-y', '-i', str(root/'speech.aiff'), '-ar', '16000', '-ac', '1', '-f', 's16le', str(root/'speech.pcm')], check=True, capture_output=True)
                pcm = (root/'speech.pcm').read_bytes() + bytes(32000)
                ticket = client.post('/api/v1/staff/roundloop/sessions', json={'subject': 'aino', 'external_synthetic_ack': True})
                ticket.raise_for_status()
                result = {'language': language, 'expected': phrase, 'events': []}
                start = time.monotonic()
                try:
                    async with asyncio.timeout(55):
                        async with connect('ws://127.0.0.1:8780' + ticket.json()['data']['path'], origin=origin, additional_headers={'Cookie': cookie}, proxy=None) as ws:
                            result['events'].append(json.loads(await ws.recv())['type'])

                            async def send():
                                for i in range(0, len(pcm), 3200):
                                    await ws.send(pcm[i:i+3200])
                                    await asyncio.sleep(.1)
                                await ws.send('{"type":"stop"}')

                            task = asyncio.create_task(send())
                            try:
                                async for raw in ws:
                                    msg = json.loads(raw)
                                    result['events'].append(msg['type'])
                                    if msg['type'] == 'transcript':
                                        result['text'] = ' '.join(s['text'] for s in msg['segments'])
                                    if msg['type'] in ('done', 'error'):
                                        break
                                await task
                            finally:
                                task.cancel()
                                await asyncio.gather(task, return_exceptions=True)
                except Exception as exc:
                    result['failure_type'] = type(exc).__name__
                result['seconds'] = round(time.monotonic()-start, 2)
                print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    asyncio.run(main())
