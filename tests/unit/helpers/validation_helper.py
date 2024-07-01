# (c) Copyright IBM Corp. 2024
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)
def LISTDS_data_set(data_set_name, dsorg):
    return """
        1READY
          LISTDS '{0}'
         {0}
         --LRECL--DSORG-
           **     {1}
         --VOLUMES-BLKSIZE
                     **
         READY
         END
    """.format(data_set_name, dsorg)


def LISTDS_data_set_doesnt_exist(data_set_name):
    return """
        1READY
            LISTDS '{0}'
           {0}
           DATA SET '{0}' NOT IN CATALOG
           READY
           END
    """.format(data_set_name)
