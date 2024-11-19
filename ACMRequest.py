from urllib.parse import quote
import DBUtils as uti


# It converts the query to be used in the URL, probably there is a better way to do this
def encode_boolean_expression(expression: str) -> str:
    if uti.target_db == uti.DB_ACM:
        expression = expression.replace(" ", "+")  
        return quote(expression, safe="+") 
    elif uti.target_db == uti.DB_IEEE    :
        return quote(expression, safe="+") 
    return quote(expression, safe="+") 


def add_parameter_to_url(url, parameter_name, parameter_value):
    parameter_connector = "&"
    parameter_assignment_str = "="
    return url + parameter_connector + parameter_name + parameter_assignment_str + parameter_value

print(encode_boolean_expression('(("All Metadata":VR) OR ("All Metadata":Virtual reality) OR ("All Metadata":augmented reality) OR ("All Metadata":AR) OR ("All Metadata":mixed reality) OR ("All Metadata":XR)) AND (("All Metadata":Multiuser) OR ("All Metadata":multi-user) OR ("All Metadata":collaborative))'))