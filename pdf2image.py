 
import pdf2image as pdf2
 
pdf2.pages

pages = pdf2.convert_from_path('C:\\01 Fox _工作區\\80 書籍pdf\\用生活常識就能看懂財務報表,林明樟著,廣州：廣東經濟出版社_14304173.pdf')

for i in range(len(pages)):
    pages[i].save('page'+ str(i) +'.jpg', 'JPEG')
