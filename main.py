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

async def send_message(text, model):  # Placeholder - implement your own
    try:
        print(f"Playing: {text}")
        waveform = model.generate(text, audio_prompt_path="prompt_audio.wav")
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

        with open("config", "r") as f:
            followers = [line.strip() for line in f if line.strip()]
        print("Following Followers are enabled:")
        print(followers)

        last_count = 0

        while True:
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            chat_items = soup.find_all('div', class_='m-chatitem')

            if len(chat_items) > last_count:
                new_item = chat_items[-1]
                username = new_item.find('div', class_='e-username').get_text(strip=True)
                message = new_item.find('div', class_='e-message').get_text(strip=True)

                if username in followers:
                    await send_message(message, model)

                last_count = len(chat_items)

            await asyncio.sleep(1)

        await browser.close()

def main():
    model = ChatterboxTurboTTS.from_pretrained(device="cuda")
    asyncio.run(check_new_element(model))

if __name__ == "__main__":
    main()

