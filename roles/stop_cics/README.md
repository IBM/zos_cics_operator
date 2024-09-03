**Stop CICS Role**
========================

The **Stop CICS Role** is responsible for stopping the specified CICS region and verifies whether the CICS region has stopped. The role issues a shutdown command and the task continues running until the region has stopped successfully. A timeout can be issued, causing the task to fail, if the region is not shut down within a certain amount of time.

