#!/bin/env python
# -*- coding: utf-8 -*-

import re, datetime, string, csv

VERSION = 0.1

class User(object):
	"""docstring for User"""
	def __init__(self, name, globalStatistics):
		
		self.name = name
		self.messages = []
		self.statistics = Statistics()
		self.globalStatistics = globalStatistics

	def addMsg(self, msg):
		self.messages.append(msg)
		self.lastMessage = len(self.messages) - 1

		# local statistics
		self.statistics.raiseMessageCount()
		self.statistics.parseText(msg.text)
		self.statistics.raiseTimeCount(msg.dTime.hour)

		# global statistics
		self.globalStatistics.raiseMessageCount()
		self.globalStatistics.parseText(msg.text)
		self.globalStatistics.raiseTimeCount(msg.dTime.hour)

	def appendToLastMsg(self, text):
		self.messages[self.lastMessage].text += text

	def showMessages(self):
		for msg in self.messages:
			msg.printMessage()


class Statistics(object):
	"""docstring for Statistics"""
	def __init__(self):
		self.reset()

	def reset(self):
		self.letters = {}
		for char in string.ascii_lowercase:
			self.letters[char] = 0

		self.time = {}
		for hour in range(24):
			self.time[hour] = 0

		self.words = {}
		self.messages = 0

	def raiseMessageCount(self):
		self.messages += 1

	def raiseTimeCount(self, hour):
		self.time[hour] += 1

	def parseText(self, text):
		# Letter stats
		for char in text:
			if char in string.ascii_letters:
				self.letters[char.lower()] += 1

		textFormat = text.strip()
		for word in textFormat.lower().split(" "):
			if word in self.words:
				self.words[word] += 1
			else:
				self.words[word] = 1
			

class Message(object):
	"""docstring for Message"""
	def __init__(self, sender, dTime, text):
		
		self.sender = sender
		self.dTime = dTime
		self.text = text

	def printMessage(self):
		print "[" + str(self.dTime) + "] " + self.sender.name + ": " + self.text[:-1]


class WhatsAppStats(object):
	"""docstring for WhatsAppStats"""
	def __init__(self, inputFile):

		self.file = inputFile
		self.users = {}
		self.globalStatistics = Statistics()

		# Chronical order
		self.chatMessages = []

	def run(self):

		# Read and parse the chatlog
		f = open(self.file,'r')
		for line in f.readlines():
			self.parseLine(line)

		f.close()

	def printChat(self):
		for msg in self.chatMessages:
			msg.printMessage()

	def printMessageCount(self):
		count = 0
		for user in self.users.values():
			count += user.statistics.messages
			print user.name + ": " + str(user.statistics.messages)

		print "Total: " + str(count) + " messages"

	def writeMessageCount(self):
		fileToSave = 'WA_MessageCount.csv'
		with open(fileToSave, 'wb') as csvfile:
			writer = csv.writer(csvfile, dialect='excel', delimiter=';')
			for user in self.users.values():
				writer.writerow([user.name] + [str(user.statistics.messages)])

		print "Wrote message count to " + fileToSave;

	def printGlobalStat(self, statDict):
		for key, value in statDict.items():
			print str(key) + ": " + str(value)

	def writeGlobalStat(self, statDict, filename):
		with open(filename, 'wb') as csvfile:
			writer = csv.writer(csvfile, dialect='excel', delimiter=';')
			for key, value in statDict.items():
				writer.writerow([key] + [str(value)])

	def printLetterStats(self):
		self.printGlobalStat(self.globalStatistics.letters);

	def writeLetterStats(self):
		fileToSave = 'WA_Letters.csv'

		self.writeGlobalStat(self.globalStatistics.letters, fileToSave)
		print "Wrote global letter stats to " + fileToSave;

	def printLetterStatsPerUser(self):
		for user in self.users.values():
			print "\n" + user.name
			for key, value in user.statistics.letters.items():
				print key + ": " + str(value)

	def writeLetterStatsPerUser(self):
		fileToSave = 'WA_LettersPerUser.csv'
		with open(fileToSave, 'wb') as csvfile:
			writer = csv.writer(csvfile, dialect='excel', delimiter=';')
			
			# Write names
			writer.writerow([''] + [u.name for u in self.users.values()])
			
			# Write letters
			for letter in self.globalStatistics.letters.keys():
				writer.writerow([letter] + [u.statistics.letters[letter] for u in self.users.values()])

		print "Wrote letter stats per user to " + fileToSave;

	def printTimeStats(self):
		self.printGlobalStat(self.globalStatistics.time);

	def writeTimeStats(self):
		fileToSave = 'WA_Time.csv'
		self.writeGlobalStat(self.globalStatistics.time, fileToSave)

		print "Wrote global time stats to " + fileToSave;

	def printTimeStatsPerUser(self):
		for user in self.users.values():
			print "\n" + user.name
			for key, value in user.statistics.time.items():
				print str(key) + ": " + str(value)

	def writeTimeStatsPerUser(self):
		fileToSave = 'WA_TimePerUser.csv'
		with open(fileToSave, 'wb') as csvfile:
			writer = csv.writer(csvfile, dialect='excel', delimiter=';')
			
			# Write names
			writer.writerow([''] + [u.name for u in self.users.values()])
			
			# Write time
			for time in self.globalStatistics.time.keys():
				writer.writerow([time] + [u.statistics.time[time] for u in self.users.values()])

		print "Wrote time stats per user to " + fileToSave;

	def printWordsStats(self):
		self.printGlobalStat(self.globalStatistics.words);

	def writeWordsStats(self):
		fileToSave = 'WA_Words.csv'
		self.writeGlobalStat(self.globalStatistics.words, fileToSave)

		print "Wrote global word stats to " + fileToSave;

	def writeWordsStatsPerUser(self):
		fileToSave = 'WA_WordsPerUser.csv'
		with open(fileToSave, 'wb') as csvfile:
			writer = csv.writer(csvfile, dialect='excel', delimiter=';')
			
			# Write names
			writer.writerow([''] + [u.name for u in self.users.values()])
			
			# Write words
			for word in self.globalStatistics.words.keys():
				writer.writerow([word] + [u.statistics.words[word] if word in u.statistics.words else '0' for u in self.users.values()])

		print "Wrote word stats per user to " + fileToSave;

	def parseLine(self, line):

		if line.strip() == "":
			return

		# Base from txt2re.com, can be optimized
		re1='((?:(?:[0-2]?\\d{1})|(?:[3][01]{1}))[-:\\/.](?:[0]?[1-9]|[1][012])[-:\\/.](?:(?:\\d{1}\\d{1})))(?![\\d])'	# DDMMYY 1
		re2='.*?'	# Non-greedy match on filler
		re3='((?:(?:[0-1][0-9])|(?:[2][0-3])|(?:[0-9])):(?:[0-5][0-9])(?::[0-5][0-9])?(?:\\s?(?:am|AM|pm|PM))?)'	# HourMinuteSec 1
		re4='.*?'	# Non-greedy match on filler
		re5='[:\s]'
		re6='(((?!:).)*)' # Sender
		re8='[:\s]'
		re9='((.*))'

		rg = re.compile(re1+re2+re3+re4+re5+re6+re8+re9,re.IGNORECASE|re.DOTALL)
		m = rg.search(line)

		if m:
			date = m.group(1)
			time = m.group(2)
			word1 = m.group(3)

			text = m.group(5)
			sender = word1.strip()
			dTime = datetime.datetime.strptime(date + time, "%d.%m.%y%H:%M:%S")

##OTHER LANGUAGE? edit here:
			# exclude some strings
			if "trat bei" in sender or "wurde entfernt" in sender or "hat die Gruppe verlassen" in sender or "hat das Thema zu" in sender or "Du bist" in sender or "hat das Gruppen" in sender:
				return

			# add a new user
			if not sender in self.users:
				self.users[sender] = User(sender, self.globalStatistics)

			tmpMsg = Message(self.users[sender], dTime, text)
			self.users[sender].addMsg(tmpMsg)
			self.chatMessages.append(tmpMsg)

			self.lastUser = sender
		else:
			self.users[self.lastUser].appendToLastMsg(line)


if __name__ == '__main__':
	import optparse
	parser = optparse.OptionParser()
	parser.usage = "%prog [options] file"
	parser.version = 1
	parser.description = ("Simple script to create some statistics from a WhatsApp group chat protocol")
	parser.epilog = "Read the README for more info"

	parser.add_option("-t", "--time", dest="time", help=("print time stats"), default=False, action="store_true")
	parser.add_option("", "--timeUser", dest="timeUser", help=("print time stats per user"), default=False, action="store_true")
	parser.add_option("-l", "--letter", dest="letter", help=("print letter stats"), default=False, action="store_true")
	parser.add_option("", "--letterUser", dest="letterUser", help=("print letter stats per user"), default=False, action="store_true")
	parser.add_option("-w", "--word", dest="word", help=("print word stats"), default=False, action="store_true")
	parser.add_option("", "--wordUser", dest="wordUser", help=("print word stats per user"), default=False, action="store_true")

	parser.add_option("-s", "--save", dest="save", help=("writes all statistics to different *.csv files. It's easy to import these in excel and create some barchars"), default=False, action="store_true")

	(options, args) = parser.parse_args()

	if len(args) != 1:
		parser.print_usage()
		exit()

	print "\n=== WhatsAppStats v" + str(VERSION) + " ===\n"
	chatStatistics = WhatsAppStats(args[0])
	chatStatistics.run()

	#chatStatistics.printChat()

	if options.save:
		chatStatistics.writeLetterStats()
		chatStatistics.writeLetterStatsPerUser()
		chatStatistics.writeTimeStats()
		chatStatistics.writeTimeStatsPerUser()
		chatStatistics.writeWordsStats()
		chatStatistics.writeWordsStatsPerUser()
		chatStatistics.writeMessageCount()
	elif options.time:
		chatStatistics.printTimeStats()
	elif options.timeUser:
		chatStatistics.printTimeStatsPerUser()
	elif options.letter:
		chatStatistics.printLetterStats()
	elif options.letterUser:
		chatStatistics.printLetterStatsPerUser()
	elif options.word:
		chatStatistics.printWordsStats()
	elif options.wordUser:
		chatStatistics.writeWordsStatsPerUser()
	else:
		chatStatistics.printMessageCount()
