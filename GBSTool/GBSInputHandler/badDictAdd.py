# string, dictionary, string, list of indices -> dictionary
# adds a list of indices to a dictionary of bad values existing within a dataset.
def badDictAdd(component, current_dict, error_msg, index_list):
    # if the component exists add the new error message to it, otherwise start a new set of component errror messages
    try:
        current_dict[component][error_msg] = index_list
    except KeyError:
        current_dict[component] = {error_msg: index_list}
    return current_dict
