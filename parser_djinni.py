
class Vacancy:
    def __init__(self, title, company, link, description):
        
        self._title = title
        self._company = company

        if link.startswith('/'):
            self._link = 'https://djinni.co' + link
        else:
            self._link = link
        


        self._description = description

    def __str__(self):
        return "-"*50 + f"\nTitle: {self._title} Company: {self._company} Description: {self._description[:10]}...\nLink: {self._link}\n" + "-"*50
    @property
    def title(self):
        return self._title
    @property
    def company(self):
        return self._company
    @property
    def link(self):
        return self._link

    @property
    def description(self):
        return self._description
    
import queue
import threading
import time
import requests
from bs4 import BeautifulSoup
class Parser:
    def __init__(self, search_query):
        
        self._base_url = "https://djinni.co/jobs/"
        self.url = f"{self._base_url}?all_keywords={search_query}"
        self._client = requests.Session()
        
        soup = BeautifulSoup(requests.get(self.url).text, 'html.parser')


        if soup.find('ul', class_='pagination'):    #Get pages
            self._pages = soup.find('ul', class_='pagination').find_all('li')[-2].get_text(strip=True)
            
            print(f"Found {self._pages} pages of results.")
        else:
            self._pages = 1
        self._task_queue = queue.Queue()    #Creating queue with pages
        for i in range(1, int(self._pages) + 1):
            self._task_queue.put(f"{self.url}&page={i}")

        self._result_queue = queue.Queue()      #Queue for results        

    def parse(self, html):
        
        soup = BeautifulSoup(html, 'html.parser')
        vacancies = []
        cards = soup.find('ul', class_='list-jobs')
        for job in cards.find_all('div', class_='job-item'):
            id = job.get('id').split('-')[-1]
            title = job.find('h2').get_text(strip=True)
            company = job.find('span').get_text(strip=True)
            link = job.find('a').get('href')
            
            description_span = job.find('span', class_='js-original-text')
            description = description_span.get_text(strip=True) if description_span else job.find('div', id=f'job-description-{id}').get_text(strip=True)
            
            vacancy = Vacancy(title, company, link, description)
            vacancies.append(vacancy)
        return vacancies

        
    def _worker(self):
        while True:
            url = self._task_queue.get()
            if url is None:
                break
            response = self._client.get(url)
            vacancies = self.parse(response.text)
            self._result_queue.put(vacancies)
                
            


    def get_all_vacancies(self, num_threads=2):
        
        for _ in range(num_threads):
            self._task_queue.put(None)
        
        
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=self._worker)
            thread.start()  
            threads.append(thread)
            
        print(f"Launched {num_threads} threads for parsing...")

        
        for thread in threads:
            thread.join()
            
        print("All threads completed execution successfully. Collecting data...")

        
        all_vacancies = []
        while not self._result_queue.empty():
            batch = self._result_queue.get()
            if batch:  
                all_vacancies.extend(batch)
                
        return all_vacancies
    

    def save_to_csv(self, vacancies, filename="vacancies.csv"):
        import csv
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Company', 'Link', 'Description'])
            for vacancy in vacancies:
                writer.writerow([vacancy.title, vacancy.company, vacancy.link, vacancy.description])
    

if __name__ == "__main__":
    start_time = time.perf_counter()
    ps = Parser("")
    
    
    vacancies = ps.get_all_vacancies(num_threads=4)
    
    
    ps.save_to_csv(vacancies)
    print(f"Total vacancies found and saved: {len(vacancies)}")

    
    execution_time = time.perf_counter() - start_time
    print(f"Parsing done in {execution_time:.2f} sec.")