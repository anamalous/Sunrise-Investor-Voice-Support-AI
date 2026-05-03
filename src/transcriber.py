import json
import os
from faster_whisper import WhisperModel

def check_audio_properties(input_path):
    valid_extensions = ('.mp3', '.wav', '.m4a', '.flac') 
    if not input_path.lower().endswith(valid_extensions):
        raise ValueError(f"Unsupported file type. Please provide: {valid_extensions}")

    if os.path.getsize(input_path) < 1000: # less than 1KB
        raise ValueError("Audio file is too small or empty.")

def transcribe_audio(input_path, output_dir):
    try:
        check_audio_properties(input_path)
        model_size = "base" # 74 million params
        
        try:
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
        except Exception as e:
            return {"error": f"Failed to load Whisper model: {str(e)}"}

        print(f"--- Processing: {input_path} ---")
        
        segments, info = model.transcribe(
            input_path, 
            beam_size=5, 
            word_timestamps=True
        )

        full_transcript = ""
        words_data = []
        
        segments = list(segments)
        if not segments or (len(segments) == 1 and not segments[0].text.strip()):
            return {"error": "Empty audio: No speech content detected."}
        
        total_conf = 0
        word_count = 0

        for segment in segments:
            full_transcript += segment.text + " "
            for word in segment.words:
                total_conf += word.probability
                word_count += 1
                words_data.append({
                    "word": word.word.strip(),
                    "start": round(word.start, 2),
                    "end": round(word.end, 2),
                    "confidence": round(word.probability, 4)
                })

        avg_confidence = total_conf / word_count if word_count > 0 else 0
        
        output_payload = {
            "metadata": {
                "language": info.language,
                "model_size": model_size,
                "avg_confidence": round(avg_confidence, 4)
            },
            "transcript": full_transcript.strip(),
            "word_segments": words_data,
            "warnings": []
        }

        if avg_confidence < 0.5: # low confidence is usually due to noise or low volume
            output_payload["warnings"].append(
                "Low audio clarity detected. Please speak louder or reduce background noise.")
            return output_payload

        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "transcript.json")
        
        with open(output_file, "w") as f:
            json.dump(output_payload, f, indent=4)
        
        return output_payload

    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        return {"error": f"System Error: {str(e)}"}

if __name__ == "__main__":
    res = transcribe_audio("input/audio-loan.mp3", "output")
    if "error" in res:
        print(f"FAILED: {res['error']}")
    else:
        if res.get("warnings"):
            print(f"WARNING: {res['warnings']}")
        else:
            print(f"SUCCESS: {res['transcript']}")