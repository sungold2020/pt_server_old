
#!/usr/bin/bash
mysqldump -uroot -pmoonbeam db_movies movies > movies.sql
mysqldump -uroot -pmoonbeam db_movies rss > rss.sql
mysqldump -uroot -pmoonbeam db_movies info > info.sql
