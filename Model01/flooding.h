  #ifndef FLOODING_H
  #define FLOODING_H

  #define DIMPAYLOAD 2
  #define STRINGPAYLOAD "abc"
  
  typedef nx_struct my_msg{
	  nx_uint16_t msg_id;
	  nx_uint8_t payload[DIMPAYLOAD];
  } my_msg_t;

  #define BSINK 1

  enum{
  AM_MY_MSG = 6,
  };

  #endif
