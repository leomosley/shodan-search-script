import json
import re
import requests
import socket
import time
import random

HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Accept-Language": "en-US,en;q=0.9",
  "Referer": "https://www.google.com/",
  "Connection": "keep-alive",
}


def format_ip(ip_int):
  """
  Converts an integer representation of an IP address to a standard IPv4 format.

  Args:
      ip_int (int): The integer representation of the IP address.

  Returns:
      str: The IPv4 address in dotted-decimal notation, or None if the input
            is not a valid integer.
  """
  try:
    ip_int = int(ip_int)  # Ensure it's an integer
    if 0 <= ip_int <= 4294967295:  # Valid range for IPv4
      octet1 = (ip_int >> 24) & 255
      octet2 = (ip_int >> 16) & 255
      octet3 = (ip_int >> 8) & 255
      octet4 = ip_int & 255
      return f"{octet1}.{octet2}.{octet3}.{octet4}"
    else:
      return None  # Invalid IP integer
  except ValueError:
    return None  # Not a valid integer

def extract_and_format_ips(file_path):
  """
  Reads a JSON file line by line, extracts the "ip" field, and formats
  it into a standard IPv4 address.

  Args:
      file_path (str): The path to the JSON file.

  Returns:
      list: A list of formatted IP addresses.
  """
  ips = []
  try:
    with open(file_path, 'r') as file:
      for line in file:
        try:
          json_object = json.loads(line.strip())
          if "ip" in json_object:
            ip_value = json_object["ip"]
            formatted_ip = format_ip(ip_value)
            if formatted_ip:
              ips.append(formatted_ip)
            else:
              print(f"Invalid IP value: {ip_value}")
        except json.JSONDecodeError:
          print(f"Skipping invalid JSON line: {line.strip()}")
        except Exception as e:
          print(f"An error occurred: {e}")
  except FileNotFoundError:
    print(f"File not found: {file_path}")
  return ips

def reverse_dns_lookup(ip_address):
  """
  Performs a reverse DNS lookup to find the domain name associated with an IP address.

  Args:
      ip_address (str): The IP address to lookup.

  Returns:
      str: The domain name, or None if the lookup fails.
  """
  try:
    hostname = socket.getfqdn(ip_address)
    if hostname != ip_address:  # Check if it's a valid domain name
      return hostname
    else:
      return None
  except socket.herror:
    print(f"No domain name found for {ip_address}")
    return None
  except Exception as e:
    print(f"Error during reverse DNS lookup for {ip_address}: {e}")
    return None

def fetch_readme_content(domain):
  """
  Fetches the content of readme.txt from the specified domain and extracts
  the plugin version.

  Args:
      domain (str): The domain to query.

  Returns:
      tuple: (url, version) or (None, None) if the request fails or version not found.
              url is the full URL to readme.txt, version is the plugin version string.
  """
  url = f"http://{domain}/wp-content/plugins/embedpress/readme.txt"
  try:
    response = requests.get(url, headers=HEADERS, timeout=5)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    content = response.text
    version_match = re.search(r"Stable tag: ([\d.]+)", content)
    if version_match:
      version = version_match.group(1).strip()
      return url, version
    else:
      print(f"Version not found in readme.txt for {domain}")
      return None, None
  except requests.exceptions.RequestException as e:
    print(f"Request failed for {domain}: {e}")
    return None, None

def version_key(item):
  """
  Key function for sorting plugin versions.
  Splits the version string into parts and converts them to integers where possible.
  """
  parts = item["version"].split(".")
  return [int(part) if part.isdigit() else part for part in parts]

def main():
  """
  Main function to extract IPs, perform reverse DNS lookup, fetch readme content,
  sort by version, and save responses to a JSON file.
  """
  
  file_path = 'input.json'
  ips = extract_and_format_ips(file_path)
  results = []
  
  for ip in ips:
    time.sleep(random.uniform(2, 6))

    domain = reverse_dns_lookup(ip)
    if domain:
      url, version = fetch_readme_content(domain)
      if url and version:
        results.append({"domain": domain, "url": url, "version": version})  # Store domain instead of IP
    else:
      print(f"No domain found for IP: {ip}")
  
  # Sort the results by plugin version (lowest first)
  results.sort(key=version_key)
  
  # Save the results to output.json
  with open('output.json', 'w') as outfile:
    json.dump(results, outfile, indent=4)
    print(f"Sites found: {len(results)}")
  print("Results saved to output.json")

if __name__ == "__main__":
  main()