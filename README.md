# duck_rice

-- REQUIREMENTS --
1. Support and manage different types of users and user profiles.
2. Support restaurant managers in creating/modifying menu and prices, coupon codes, etc.
3. Support restaurant staff in managing and fulfilling orders
4. Support customer in browsing menu, placing an order, and makes their payment from the table.
5. Support restaurant owners in collecting and organising data that can be used for marketing efforts. This
includes customers’ behaviour and patterns such as average spend per visit, frequency/patterns of visits
(or how long since they last visited) and preferences for dishes/drinks. These insights can be used for
personalised marketing such as tailoring specials to specific customers.


-- FILES --
classes.py : put all BCE classes here
main.py : backend logic using BCE from classes.py
database.uxf : UMLet diagrams for database
create.psql : CREATE statements for database


-- FOLDERS --
__pycache__ : ignore this
pm_project-master : reference from previous csit214 project using flask
templates : put all HTML files here



-- HOW TO RUN --
pip install flask psycopg2 (install modules)
python main.py (run webserver on localhost:5000)
(if it has error 'ModuleNotFound', run "pip install <Module>")
