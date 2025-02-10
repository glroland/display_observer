install:
	pip install -r requirements.txt

clean:
	rm -f target/frame*.jpg

text_from_frame:
	cd src && python text_from_frame_app.py

image_diff:
	cd src && python image_diff_app.py
