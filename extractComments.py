''' Michael Wang
This is a simple Python script to 
1. Extract the commentPreprocessed comments out of a Youtube json comment file
2. Detect non English comments
3. Translate non English comments to English comments
4. Output back to json file with new field commentTranslated
5. Output translated texts and the languages they were translated from in a log file output.log
'''
import json
import sys
import subprocess

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print("Usage: python extractComments.py filename")
		sys.exit(0)

	# Open file to read from
	filename = sys.argv[1]
	with open(filename) as f:
	    data = json.load(f)

	output_file = open("output.log", "w+")

	# Write to comments list
	comments = []
	for i in range(len(data)):
		comments.append((json.dumps(data[i][0]["commentPreprocessed"]) + "\n", i))
	
	# Check the language of each comment
	translate = []
	for pair in comments:
		comment   = pair[0] # Actual comment itself
		print(comment)
		json_line = pair[1] # Line in json which comment is on

		# Try detecting the language and if it is not English, add it to a list to be translated
		try:
			result = subprocess.check_output(['python3.6','translate.py','detect-language', comment])
			for line in result.split("\n"):
				if line.startswith("Language"):
					language = line[10:]
					if language != "en":
						comment = comment.replace("\"", ""); # Remove the quotes from the string
						translate.append((comment.rstrip(), json_line))
					break
		except:
			output_file.write("Unable to detect language for " + comment + "\n")
			print("Unable to detect language for " + comment)

	print("List of words to be translated")
	print(translate)

	if not translate:
		print("All comments in English")
	else:
		for pair in translate: # Translate non English languages
			comment   = pair[0] # Actual comment itself
			json_line = pair[1] # Line in json which comment is on

			# Try translating given comment to English
			try:
				# Translate 
				result = subprocess.check_output(['python3.6','translate.py','translate-text', "en", comment])
				for line in result.split("\n"):
					if line.startswith("Translation"):
						translation = line[13:]
						output_file.write("Original comment: " + comment + "\n")
						output_file.write("Translated Comment: " + translation + "\n")
						new_data = {"commentTranslated": translation}
						data[json_line][0].update(new_data)
					if line.startswith("Detected"):
						output_file.write(line + "\n\n")
			except:
				output_file.write("Unable to translate " + comment + " to English\n")
				print("Unable to translate " + comment + " to English")


	with open(filename, 'w') as f:
		json.dump(data, f)