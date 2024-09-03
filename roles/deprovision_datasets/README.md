**Deprovision Datasets Role**
========================

The **Deprovision Datasets Role** provides automation for deleting each of the region data sets and the DFHSTART data set at the templated location or user-specified location provided. The list of data sets deleted are as follows:

* Auxiliary trace data set (DFHAUXT)
* Second auxiliary trace data set (DFHBUXT)
* Transaction dump data set (DFHDMPA)
* Second transaction dump data set (DFHDMPB)
* CSD data set (DFHCSD)
* Transient data intrapartition data set (DFHINTRA)
* Local request queue data set (DFHLRQ)
* Global catalog data set (DFHGCD)
* Local catalog data set (DFHLCD)
* Auxiliary temporary storage data set (DFHTEMP)
* CICS startup JCL (DFHSTART)
