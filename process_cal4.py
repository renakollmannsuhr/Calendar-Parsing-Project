#!/usr/bin/env python3
"""
proccess_cal4.py represents the process_cal class and all it's supported method

Most recent update by  Rena Kollmann-Suhr on 12/06/2021


"""



import re
import datetime

class process_cal:
    """
    class with attribute filename
    opens a calendar ics file and parses 
    """
    def __init__(self,filename):
        """
        creates instance of process_cal and assigns a filename attribute
        """
        self.__filename=filename

    def get_events_for_day(self, day):
        """
        takes the datetime object and checks to see if there are any events for that
        date in the ICS file received and if found, returns a string with the day’s
        events

        If the day corresponding to the datetime object parameter has events, then 
        the method returns a string with that day’s events.

        If the day corresponding to the datetime object parameter has no events, then
        None is returned by the method.
        """
        file_handle = open(self.__filename,"r")
        lines = file_handle.readlines() #list of lines as strings
       
        dict_list=[]
        list_events = self.make_dicts(1,lines,dict_list) #returns a list of dictionary events
 
        #creates a copy of the event list, so changes made will not affect original dictionry events        
        index = 0
        list_copy = list_events.copy()
        for event in list_copy:

                if "RRULE" in event: #checks if current event is a repeating one
                        events_to_add = self.make_dicts_repeating(list_events,event)
                        list_events.remove(event)
                        list_events += events_to_add
                index+=1
        
        events_str = "" 

        #loop through each event dictionary in list, extract relevant data using regexes, then print event if it occurs on current day
        
        prev = [] #prev is a list of start dates of the events last visited that matched current day, so that events occuring on same day pint differently
        for event in list_events:
            start_str = event["DTSTART"]
            end_str = event["DTEND"]
            summary = event["SUMMARY"]
            location = "{" + event["LOCATION"]+"}" 
            pattern = re.compile(r"^(\d\d\d\d)(\d\d)(\d\d)T(\d\d)(\d\d)(\d\d)")
            match = pattern.search(start_str)
            
            
            #create start date object
            event_start_dt = datetime.datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            #create end date object
            match_end = pattern.search(end_str)
            event_end_dt = datetime.datetime(int(match_end.group(1)), int(match_end.group(2)), int(match_end.group(3)),int(match_end.group(4)),int(match_end.group(5)),int(match_end.group(6)))
            
            if event_start_dt == day:
                 #store last_date visited that matched current date
                 if len(prev)!=0:
                     last_date =prev[-1]
                 
                 #creates formatted start date string
                 format_start = self.format_date(event_start_dt)
                 
                 #creates a divider with the same length as formatted start date string
                 divider = self.construct_divider(format_start)

                 # recreate datetime object, this time with time included
                 event_start_dt = datetime.datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)),int(match.group(4)),int(match.group(5)),int(match.group(6)))
                 
                 #create formatted start time and end time strings
                 start_t = self.format_time(event_start_dt)
                 end_t = self.format_time(event_end_dt)
            #    print(event_start_dt.strftime("%I:%M %p"))
                 
                 if (len(prev)==0 or start_str[:7]!=last_date[:7]):   
                     events_str += f'{format_start}\n{divider}\n{start_t} to {end_t}: {summary} {{{location}}}' 
                 else:
                     events_str += f'\n{start_t} to {end_t}: {summary} {{{location}}}' 
                 
                 prev.append(start_str)
        if events_str!="":
            return events_str
        else:
            return None
  
    def format_date(self,dt):
        """
        returns formatted string of datetime object in the form: February 14, 2021 (Sun)
        """
        return dt.strftime("%B %d, %Y (%a)")

    def construct_divider(self,dt_format):
        """
        creates a divider with the same length as formatted formatted date string
        """
        return '-'*len(dt_format)

    def format_time(self,dt):
        """
        #creates and retruns a formatted time string: 9:00 PM
        """
        if dt.strftime("%I:%M %p").startswith("0"):
            return dt.strftime(" %-I:%M %p")
        else:
            return dt.strftime("%-I:%M %p")

    def make_dicts(self,line_num,lines,dict_list):
        """
        creates a dictionary for each event encountered in ics file, recursivley calls
        itself to creat and append more dictionaries to list.
        returns the list of all dictionaries, each representing an event.
        """

        dict_cal={}
      
        # adds only first line with BEGIN to dict
        line = lines[line_num]
        pattern = re.compile(r'^(.+):(.+)')
        match = pattern.search(line)
        #line_without_newline = lines[line_num].rstrip()
        #split = line_without_newline.split(':')
        dict_cal[match.group(1)]=match.group(2)
  
        # adds second line to dict
        line_num+=1
        line_without_newline = lines[line_num].rstrip()
        split = line_without_newline.split(':')
        dict_cal[split[0]]=split[1]
        line_num+=1

        if split[1]=="VEVENT" and split[0]=="BEGIN":
            line_without_newline = lines[line_num].rstrip()
            split = line_without_newline.split(':')
            dict_cal[split[0]]=split[1]
            line_num+=1

        #loop creates dictionary until next event hit
        while line_num < len(lines) and split[1]!="VEVENT" and split[0]!="BEGIN":
            line_without_newline = lines[line_num].rstrip()
            split = line_without_newline.split(':')
            dict_cal[split[0]]=split[1]
            line_num+=1

        #adds event to list event
        dict_list.append(dict_cal)
 
        #if there's a new event, recursively calls function to create next dictionary
        if line_num < len(lines)-3 and split[0]=="END" and split[1]=="VEVENT":
            self.make_dicts(line_num,lines,dict_list)        

        return dict_list

    def  make_dicts_repeating(self,list_events, repeating_event):
        '''
        will create dictionary for the repeating event for each day it is repeated
        returns list of the new dictionaries created
        '''

        rrule_str = repeating_event["RRULE"]
        rrule_split = rrule_str.split(";")

        for element in rrule_split:
                if "UNTIL" in element:
                        until_date = datetime.datetime.strptime(element[6:],'%Y%m%dT%H%M%S')
        date_start_obj = datetime.datetime.strptime(repeating_event["DTSTART"],'%Y%m%dT%H%M%S')
        delta = datetime.timedelta(days=7)
        events_to_add = []

        while date_start_obj <= until_date:
                repeating_event["DTSTART"]=date_start_obj.strftime("%Y%m%dT%H%M%S")
                events_to_add.append(repeating_event.copy())#append copy of dictionary so original does not change original 
                date_start_obj+=delta

        return events_to_add


