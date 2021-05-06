import requests
from jira import JIRA
import urllib3
import mapping
import webbrowser
import time

urllib3.disable_warnings()

#Logindaten überprüfen. Liefert "True" wenn Login möglich, "False" falls Passwort falsch
def login_check(user, password):
    try:
        login = requests.get('https://siemconp001.srv.muenchen.de/api/siem', verify=False, auth=(user,password))
        login = login.status_code
        if login != 401:
            return True
        else:
            return False
    except:
        return False

#mainClass enthält alle wichtigen Daten, die während der Laufzeit des Programms benötigt werden
class Main:
    
    def __init__(self, user, password):
    
        self.user = user
        self.password = password
        
        #Liste mit allen offenen Offenses von Qradar (jedes Offense ist eine Klasse)
        self.openOffensesList = self.get_open_offenses()
        
        #Das jiraObject beinhaltet alle Funktionen der jira-Bibilothek:
        self.jiraObject = self.get_jira_object()
        self.casesList = self.get_cases()
        
        #Beinhaltet das Mapping der Felder, da Jira-Cases nur den Namen "Customfield..." kennen -> z.B. "LHM Qradar Offense":"Customfield000111"
        allfields = self.jiraObject.fields()
        self.nameMap = {field['name']:field['id'] for field in allfields}
        
        #Dictionary mit OffenseId:CaseId -> ist kein Case vorhanden Offense:False
        self.offensesWithCase = self.get_offenses_with_case()
        
    def get_open_offenses(self):
        headers = {
            'Range': 'items=0-1000',
            'Version': '12.1',
            'Accept': 'application/json',
            }
        params = (('filter', 'status="OPEN"'),)

        responseQradar = requests.get('https://siemconp001.srv.muenchen.de/api/siem/offenses', verify=False, headers=headers, params=params, auth=(self.user, self.password))
        openOffensesQradar = responseQradar.json()
        openOffenses = []      
        for offenseJson in openOffensesQradar:
            offense = Offense(offenseJson)
            openOffenses.append(offense)
        return openOffenses
        
    def get_jira_object(self):
        options = {'server': 'https://csccmp001.srv.muenchen.de:8443/jira','verify': False}
        jira = JIRA(options, basic_auth=(self.user, self.password))
        return jira
        
    def get_cases(self):
        block_size = 100
        block_num = 0
        issues = []

        while True:

            start_idx = block_num * block_size
            if block_num == 0:
                issues = self.jiraObject.search_issues('project=10100', start_idx, block_size)
            else:
                more_issue = self.jiraObject.search_issues('project=10100', start_idx, block_size)
                if len(more_issue)>0:
                    for x in more_issue:
                        issues.append(x)
                else:
                    break
            if len(issues) == 0:
                # Retrieve issues until there are no more to come
                break
            block_num += 1
            return issues
        
    def get_offenses_with_case(self):
        offensesWithCase = {}
        for offense in self.openOffensesList:
            offensesWithCase.update({offense.id:False})
            for issue in self.casesList:
                try:
                    if int(offense.id) == int(getattr(issue.fields, self.nameMap['LHM QRadar Offense - Id'])):
                        offensesWithCase.update({offense.id:issue.key})
                    else:
                        pass
                except:
                    pass
        return offensesWithCase
        
    def get_offense_object(self, offenseId):
        for offense in self.openOffensesList:
            if offense.id == offenseId:
                return offense
                
    def create_case(self, updateDictionary):
        caseInformationDict = {'project': {'key': 'CSCCM'},
                           'issuetype': {'name': 'CSC-A04 Case'}}
                        
        for key in updateDictionary:
                caseInformationDict.update({self.nameMap[key]:updateDictionary[key]})
            
        new_issue = self.jiraObject.create_issue(fields=caseInformationDict)
        
        urlCreatedCase = "https://csccmp001.srv.muenchen.de:8443/jira/secure/EditIssue!default.jspa?id=" + str(new_issue.id)
        time.sleep(3)
        webbrowser.open(urlCreatedCase)
                
#Klasse für Offense
class Offense:

    def __init__(self, offenseJson):
        for caseFieldName in mapping.mapping:
                setattr(self, str(mapping.mapping[caseFieldName][0]), str(offenseJson[mapping.mapping[caseFieldName][0]]).replace("\n", " "))
    




