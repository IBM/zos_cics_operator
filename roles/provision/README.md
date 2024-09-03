**Provision Role**
========================

The **Provision Role** is a high level role that calls lower level roles sequentially, providing automation for CICS region provisioning operations. This role creates region data sets, a zFS data set, and start a CICS region using these data sets. The role also creates a DFHSTART data set that stores the startup JCL used for the initialization of the CICS region.
