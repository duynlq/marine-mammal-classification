import os
import requests
import time
import shutil
import re
from CREDENTIALS import DOLBYIO_API_KEY


def upload_audio():
    file_path = "training_data_test"
    uploaded_files = {}

    for mammal in os.listdir(file_path):
        mammal_path = os.path.join(file_path, mammal)

        # Skip if it's not a directory (avoid stray files)
        if not os.path.isdir(mammal_path):
            continue 

        # Initialize list for this mammal category
        uploaded_files[mammal] = []

        for file in os.listdir(mammal_path):
            # Skip non-audio files
            if not file.endswith((".wav", ".mp3", ".flac")):
                continue

            file_path = os.path.join(mammal_path, file)
            url = "https://api.dolby.com/media/input"
            headers = {
                "Authorization": "Bearer {0}".format(DOLBYIO_API_KEY),
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            # Remove spaces for URL safety
            file_safe = file.replace(" ", "_")
            body = {"url": f"dlb://in/{file_safe}"}

            response = requests.post(url, json=body, headers=headers)
            response.raise_for_status()
            data = response.json()
            presigned_url = data["url"]

            print(f"Uploading {file_path} to {presigned_url}")
            with open(file_path, "rb") as input_file:
                requests.put(presigned_url, data=input_file)

            # Store file under mammal name
            uploaded_files[mammal].append(body["url"])  

    return uploaded_files
    # Returns { "Humpback_Whale": ["dlb://in/file1.wav", "dlb://in/file2.wav"], ... }


def start_enhancement(files):
    jobs = {}

    for file in files:
        job_id = post_media_enhance(file)
        jobs[file] = {"job_id": job_id, "status": "Pending"}

    return jobs


def post_media_enhance(file_url):
    DOLBY_ENHANCE_URL = "https://api.dolby.com/media/enhance"

    body = {
        "input": file_url,
        # "output": f"dlb://out/{file_url.split('/')[-1]}.enhance.wav"
        "output": f"dlb://out/{file_url.replace('.wav', '', 1)}enhance.wav"
    }
    print(body)

    headers = {
        "Authorization": "Bearer {0}".format(DOLBYIO_API_KEY),
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(DOLBY_ENHANCE_URL, json=body, headers=headers)
    response.raise_for_status()
    return response.json()


def check_job_status(jobs):
    while True:
        active_jobs = False

        for file, job in jobs.items():
            if job["status"] in {"Pending", "Running"}:
                response = get_job_status(job["job_id"])
                jobs[file]["status"] = response["status"]

                if response["status"] in {"Pending", "Running"}:
                    active_jobs = True
                else:
                    jobs[file]["response"] = response

        if not active_jobs:
            break  # Exit when all jobs are complete
        time.sleep(5)

    return jobs


def get_job_status(job_id):
    DOLBY_ENHANCE_URL = "https://api.dolby.com/media/enhance"

    headers = {
        "Authorization": "Bearer {0}".format(DOLBYIO_API_KEY),
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.get(DOLBY_ENHANCE_URL, params={"job_id": job_id}, headers=headers)
    response.raise_for_status()
    return response.json()


def download_files(output_paths, mammal):
    DOLBY_OUTPUT_URL = "https://api.dolby.com/v1/media/output"

    mammal_output_path = os.path.join("training_data_enhanced", mammal)
    os.makedirs(mammal_output_path, exist_ok=True)  # Create mammal-specific folder

    headers = {
        "Authorization": "Bearer {0}".format(DOLBYIO_API_KEY),
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    for idx, file_url in enumerate(output_paths):
        # Ensure that file_url is fully formatted and includes the correct URL
        if not file_url.startswith("dlb://out/"):
            print(f"Skipping invalid URL: {file_url}")
            continue

        output_filename = os.path.join(mammal_output_path, f"enhanced_{idx}.wav")
        print(f"Downloading {file_url} to {output_filename}")

        response = requests.post(DOLBY_OUTPUT_URL, params={"url": file_url}, headers=headers)
        response.raise_for_status()

        with open(output_filename, "wb") as output_file:
            shutil.copyfileobj(response.raw, output_file)

        print(f"Downloaded {file_url} to {output_filename}")


if __name__ == "__main__":

    print("Uploading audio files...")
    uploaded_files = upload_audio()

    print("Starting enhancement process...")
    all_jobs = {}  # Store jobs categorized by mammal
    for mammal, files in uploaded_files.items():
        # print(files)
        all_jobs[mammal] = start_enhancement(files)

    # print("Checking job status...")
    # for mammal, jobs in all_jobs.items():
    #     completed_jobs = check_job_status(jobs)

    #     print(f"Downloading enhanced files for {mammal}...")
    #     output_files = [job["response"]["output"] for job in completed_jobs.values() if "output" in job["response"]]
    #     download_files(all_jobs, mammal)  # Pass mammal name to organize files

    print("Processing complete! Please check results!")
