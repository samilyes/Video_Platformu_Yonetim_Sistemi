# app/modules/module_2/implementations.py
from app.modules.module_2.base import BaseClass2

class Base2SubClass1(BaseClass2):
    def method2(self):
        print(f"Sinif Attribute: {self.base2Attribute}")

class Base2SubClass2(BaseClass2):
    def method2(self):
        print(f"Sinif Attribute: {self.base2Attribute}")