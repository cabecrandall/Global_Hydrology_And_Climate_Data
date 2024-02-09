"""
Cannot be run, these functions specific to GAGES
hydrology data may be imported to another module to help
with common inconsistencies in processing the data.
"""

def verify_column_type(df, id_column, type):
    """
    This function verifies that the column type of the id_column is numeric
    :param df: a pandas dataframe
    :param id_column: the column to verify
    :param type: the type to verify
    :return: the original dataframe if the column's type matches
        the type parameter, otherwise the dataframe column is
        converted to the type parameter and returned.
    """
    if df[id_column].dtype != type:
        df = df.astype({id_column: type})
    return df

def add_leading_zeroes(df, id_column, string):
    """
    This function adds leading strings to the id_column of a dataframe
    :param df: a pandas dataframe
    :param id_column: the column to add leading zeroes to
    :param zeroes: the number of leading zeroes to add
    :return: the original dataframe with the id_column modified
    """
    # TODO: make it conditional on string length
    df[id_column] = df[id_column].apply(lambda x: str(x).zfill(string))
    return df