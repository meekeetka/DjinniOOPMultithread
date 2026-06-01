# Djinni Multithreaded Job Parser

A simple multithreaded parser for Djinni using `requests` and `beautifulsoup4`. It uses a thread pool to process pages in parallel to speed up network requests. The script tracks execution time, demonstrating a massive performance boost compared to its synchronous analog.

It is not recommended to use more than 4 threads without a proxy because of the Djinni anti-DDoS system. Otherwise, you will get banned by IP. You can bypass this limitation by using a proxy pool.

The `Vacancy` class is actually useless and was written just to practice OOP concepts. It simply stores the job title, company name, link, and description.

## Requirements

* Python 3.10+
* beautifulsoup4 == 4.12.3
* requests == 2.32.3
