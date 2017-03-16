# -*- coding: utf-8 -*

from Products.CMFCore.WorkflowCore import WorkflowException


def create_content(root, content):
    """ Create content from a list of dicts, recursively
    """
    for item in content:

        if item.has_key('options'):
            options = item['options']
            del item['options']

        if not root.get(item['id']):
            root.invokeFactory(**item)

        obj = root[item['id']]

        for option,value in options.items():
            if option == 'do_workflow':
                try:
                    root.portal_workflow.doActionFor(obj, value)
                except WorkflowException:
                    print '[Warning] WorkflowException: Can\'t %s %s' %(value, root.id)
                    
            elif option == 'contains':
                create_content(obj, value)
            elif option == 'allowed_types':
                obj.setConstrainTypesMode(True)
                obj.setLocallyAllowedTypes(value)
            elif option == 'view_template':
                obj.setLayout(value)