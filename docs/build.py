from os import system

system("sphinx-build -b gettext ./source build/gettext")
system("sphinx-intl update -p build/gettext -l en")
system("sphinx-build -b html -D language=zh_CN ./source build/html/zh_CN")
system("sphinx-build -b html -D language=en ./source build/html/en")
