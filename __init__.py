from datetime import datetime, timedelta
from mycroft import MycroftSkill, intent_handler
from mycroft.util.parse import extract_datetime
from mycroft.messagebus.client import MessageBusClient


class ArztterminSkill(MycroftSkill):
    def __init__(self):
        super(ArztterminSkill, self).__init__()

    def initialize(self):
        pass

    @intent_handler('Reminder.intent')
    def add_unspecified_reminder(self, msg=None):        
        # TIME:
        time_response = self.get_response('ParticularTime', on_fail='wait.for.answer', num_retries=20)
        # Check if a time was in the response
        dt, rest = extract_datetime(time_response) or (None, None)
        if dt or self.response_is_affirmative(time_response):
            if not dt:
                # No time specified
                time = self.get_response('ParticularTime', on_fail='wait.for.answer', num_retries=20)
                dt, rest = extract_datetime(time) or None, None
                if not dt:
                    self.speak_dialog('Fine')
                    return

        time = datetime.strftime(dt, "%H:%M")

        # DATE:
        date = None
        date_response = self.get_response('ParticularDate', on_fail='wait.for.answer', num_retries=20)
        months = ['januar', 'februar','märz', 'april', 'mai', 'juni', 'juli', 'august', 'september','oktober','november','dezember',
                'januar.', 'februar.','märz.', 'april.', 'mai.', 'juni.', 'juli.', 'august.', 'september.','oktober.','november.','dezember.', '. erster', '. ersten', '. zweiter','. zweiten' ,'. dritter', '. dritten','. 3','. 4','. 5','. 6','. 7','. 8','. 9','. 10','. 11','. 12','. 13','. 14','. 15',
                '. 16','. 17','. 18','. 19','. 20','. 21','. 22','. 23','. 24','. 25','. 26','. 27','. 28','. 29','. 30','. 31']
        days = ['erster', 'ersten', 'zweiter','zweiten' ,'dritter', 'dritten','3','4','5','6','7','8','9','10','11','12','13','14','15',
                '16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
        day = [d for d in days if(d in date_response.lower())]
        month = [m for m in months if(m in date_response.lower())]

        if (bool(day) and bool(month)):
            date = day[-1] + '. ' + month[-1]
        else:
            # TODO: besser nach wiederholung fragen
            date_response = self.get_response('ParticularDateTwo', on_fail='wait.for.answer', num_retries=20)
            day = [d for d in days if(d in date_response)]
            month = [m for m in months if(m in date_response)]
            date = day[-1] + '. ' + month[-1]

        # NAME:
        name = self.get_response('ParticularName', on_fail='wait.for.answer', num_retries=20)
        name = name.lower().replace('der', '').replace('termin', '').replace('ist', '').replace('bei', '').replace('er heißt', '').replace('ich', '').replace('glaube', '').replace('dieser', '').replace('mein', '').replace('arzttermin', '').replace('arzt', '').replace('ärztin', '')

        if (time is None):
            time_response = self.get_response('ParticularTime', on_fail='wait.for.answer', num_retries=20)
            # Check if a time was in the response
            dt, rest = extract_datetime(time_response) or (None, None)
            if dt or self.response_is_affirmative(time_response):
                if not dt:
                    # No time specified
                    time = self.get_response('ParticularTime', on_fail='wait.for.answer', num_retries=20)
                    dt, rest = extract_datetime(time) or None, None
                    if not dt:
                        self.speak_dialog('Fine')
                        return
                # self.__save_reminder_local(time, dt)
            else:
                self.log.debug('put into general reminders')
                # self.__save_unspecified_reminder(reminder)

            time = datetime.strftime(dt, "%H:%M")
        if (name is None):
            name = self.get_response('ParticularName', on_fail='wait.for.answer', num_retries=20)
            name = name.lower().replace('der', '').replace('termin', '').replace('ist', '').replace('bei', '').replace('er heißt', '').replace('ich', '').replace('glaube', '').replace('dieser', '').replace('mein', '').replace('arzttermin', '').replace('arzt', '').replace('ärztin', '')
        if (date is None):
            date_response = self.get_response('ParticularDate', on_fail='wait.for.answer', num_retries=20)
            months = ['januar', 'februar','märz', 'april', 'mai', 'juni', 'juli', 'august', 'september','oktober','november','dezember']
            days = ['erster', 'ersten', 'zweiter','zweiten' ,'dritter', 'dritten','3','4','5','6','7','8','9','10','11','12','13','14','15',
                '16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
            day = [d for d in days if(d in date_response.lower())]
            month = [m for m in months if(m in date_response.lower())]

            if (bool(day) and bool(month)):
                date = day[-1] + '. ' + month[-1]
        
        if (time is None or date is None or name is None):
            self.speak_dialog('confirm.without.variables')
        else:
            self.speak_dialog('confirm_arzttermin', data={'time' : time, 'date': date, 'name': name})



        # Nachfrage nach weiteren Optionen (unspezifisch):
        self.speak_dialog('vorschlaege')

    def stop(self, message=None):
        if self.__cancel_active():
            self.speak_dialog('ReminderCancelled')
            return True
        else:
            return False

    def shutdown(self):
        if isinstance(self.bus, MessageBusClient):
            self.bus.remove('speak', self.prime)
            self.bus.remove('mycroft.skill.handler.complete', self.notify)
            self.bus.remove('mycroft.skill.handler.start', self.reset)


def create_skill():
    return ArztterminSkill()
