import torchaudio as ta
from flask import Flask, request, send_file
from chatterbox.tts_turbo import ChatterboxTurboTTS
import torchaudio
import torch
import io
import sounddevice as sd
import scipy.io.wavfile as wavfile
from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup
import random

async def send_message(text, audio_prompt_path, model):  # Placeholder - implement your own
    try:
        print(f"Playing: {text}")
        waveform = model.generate(text, audio_prompt_path=audio_prompt_path)
        waveform = waveform.squeeze()
        sample_rate = getattr(model, 'sr', 24000)
        sd.play(waveform.cpu().numpy(), sample_rate)
        sd.wait()
    except Exception as e:
        print(e) 

async def check_new_element(model):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://chatoverlay.colinhorn.co.uk/?twitch=baba_hier&kick=baba-hier&badges=true&monochrome=false")

        config_file = open("config", "r")

        last_count = 0

        while True:
            config_file.seek(0)
            followers = dict(line.strip().split(",") for line in config_file if line.strip())
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            chat_items = soup.find_all('div', class_='m-chatitem')

            if len(chat_items) > last_count:
                new_item = chat_items[-1]
                username = new_item.find('div', class_='e-username').get_text(strip=True)
                message = new_item.find('div', class_='e-message').get_text(strip=True)

                if username in followers:
                    await send_message(message, followers[username], model)

                last_count = len(chat_items)

            await asyncio.sleep(1)

        await browser.close()

def main():
    model = ChatterboxTurboTTS.from_pretrained(device="cuda")
    asyncio.run(check_new_element(model))

if __name__ == "__main__":
    main()

