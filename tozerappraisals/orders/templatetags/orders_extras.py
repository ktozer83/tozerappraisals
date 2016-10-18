from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

# Formats phone number to (nnn)nnn-nnnn
@register.filter(name='phonenumber')
def phonenumber(phone):
    return "(%s%s%s)%s%s%s-%s%s%s%s" % tuple(list(phone))

# Gets human readable status
@register.filter
def get_status(num):
    status = {
        0: 'Pending',
        1: 'In Progress',
        2: 'Completed',
        3: 'Cancelled',
        4: 'See Comments'
    }
    
    return status[num]