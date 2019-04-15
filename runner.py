import lxml.etree as ET

dom = ET.parse("input/house.xml")
xslt = ET.parse("XSLT/transformation.xsl")
transform = ET.XSLT(xslt)
newdom = transform(dom)
print(ET.tostring(newdom, pretty_print=False))