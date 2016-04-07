#include "flooding.h"

configuration FloodingPartAppC {}

implementation{

	components MainC;
	components FloodingPartC as App;
	components new TimerMilliC() as Timer1;
	components new AMSenderC(AM_MY_MSG) as RadioAM;
	components new AMReceiverC(AM_MY_MSG);
	components ActiveMessageC;
	components RandomC;
	components RandomMlcgC;

	//Boot Interface
	App.Boot -> MainC.Boot;
	App.RadioControl -> ActiveMessageC;

	//Timer Interface
	App.TimerSink -> Timer1;

	//Packets
	App.RadioPacket -> RadioAM;
	App.AMPacket -> RadioAM;

	//Send
	App.RadioAMSend -> RadioAM;

	//Receive
	App.Receive -> AMReceiverC;

	//Random
	App.Random -> RandomC;
	App.Seed -> RandomMlcgC.SeedInit;




}

