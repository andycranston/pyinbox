All: /usr/local/bin/smua $(HOME)/www/html/~arris53/inbox.py $(HOME)/www/html/~arris53/inbox.css $(HOME)/www/html/~arris53/trash.png
	@sleep 1
	touch All

/usr/local/bin/smua: smua.c
	gcc -o /usr/local/bin/smua smua.c
	chmod u+s,g+s /usr/local/bin/smua

smua.c:

$(HOME)/www/html/~arris53/inbox.py: inbox.py
	cp inbox.py $(HOME)/www/html/~arris53/inbox.py

inbox.py:

$(HOME)/www/html/~arris53/inbox.css: inbox.css
	cp inbox.css $(HOME)/www/html/~arris53/inbox.css

inbox.css:

$(HOME)/www/html/~arris53/trash.png: trash.png
	cp trash.png $(HOME)/www/html/~arris53/trash.png

trash.png:
