#include "Timer.h"
#include "flooding.h"
#include "memory.h"


module FloodingPartC @safe() {
	uses{
		interface Boot;
		interface Timer<TMilli> as TimerSink;
		interface Timer<TMilli> as RandomTimer; 
		interface SplitControl as RadioControl;
		interface Packet as RadioPacket;
		interface AMPacket;
		interface AMSend as RadioAMSend;
		interface Receive;
		interface Random;
		interface ParameterInit<uint16_t> as Seed;
	}
}

implementation{

	message_t packet;
	my_msg_t* recv_msg;
	uint8_t counter=0; //for ID of packets sent from SINK very 60sec
	uint8_t recv_id=0;
	bool recv_pack[255];
	bool timer_pack[255];
	uint32_t randomTimer=0;
	nx_uint8_t temp_id;
	nx_uint8_t temp_payload[DIMPAYLOAD];

	task void broadcastSink();
	task void broadcastNode();

	int sinkCounter=0;

	//----------- BOOT ------------
	//call start() on the SpliControl that is wired to ActiveMessageC
	event void Boot.booted() {

		uint16_t seed;
		FILE* f;
		f = fopen("/dev/urandom", "r");
		fread(&seed, sizeof(seed), 1, f);
		fclose(f);
		
		call Seed.init(seed+TOS_NODE_ID+1);
	
		call RadioControl.start();
	}

	//----------- RADIO TURNED ON EVENT -----------
	event void RadioControl.startDone(error_t err){
		if(err == SUCCESS){
			if(TOS_NODE_ID == 0){
				//If I am the SINK, then I have to start a periodic timer each 60sec
				dbg("boot", "I'm the SINK node with id %d and my RADIO is ON \n", TOS_NODE_ID);
				call TimerSink.startPeriodic(10000);
			}
			else{
				dbg("boot", "I'm a NODE with id %d and my RADIO is ON \n", TOS_NODE_ID);
			}
		}
		else{
			dbg("boot", "I'm NODE %d and I have to start again my RADIO", TOS_NODE_ID);
			call RadioControl.start();		
		}
		

	}

	//----------- RADIO TURNED OFF EVENT -----------
	event void RadioControl.stopDone(error_t){
	}

	//----------- SINK TIMER FIRES -----------
	//When the timer fires, the SINK sends a broadcast message
	event void TimerSink.fired(){
		sinkCounter++;
		dbg("sink", "\n");
		dbg("sink", "COUNTER: %d \n", sinkCounter);
        dbg("sink", "@@@@@@@@@@@@@@@@@@ NEW PACKET FROM SINK EACH 60s  @@@@@@@@@@@@@@@@@@@@@@@@\n");
		dbg("sink", "I'm the SINK and I post a task for sending a broadcast packet \n");
		post broadcastSink();
	}
	

	//----------- 	SEND DONE EVENT -----------
	event void RadioAMSend.sendDone(message_t* buf, error_t err){
		if(&packet == buf && err == SUCCESS){
			dbg("Packet sent done at time %s \n", sim_time_string());
		}
	}

	//----------- RECEIVE EVENT --------------
	event message_t* Receive.receive(message_t* buf, void* payload, uint8_t len){

		if(TOS_NODE_ID == 0){
			dbg("recv", "\n");
			dbg("recv", "Packet received by SINK. \n");
			dbg("recv", "DROPPING THE PACKET... \n");
		}
		else{
			dbg("recv","\n");
			dbg("recv", "I'm node %d and I've received a packet from Node %d \n", TOS_NODE_ID, call AMPacket.source(buf));
			dbg("recv", "\t Time of reception: %s \n", sim_time_string());

			//check the content of the packet
			recv_msg = (my_msg_t*)payload;
		

			//dbg("recv", "\t The TYPE of the message is: %hhu \n", recv_msg->msg_type);
			dbg("recv", "\t The ID of the message is: %d \n", recv_msg->msg_id);

			dbg("recv", "RECV FROM %d PACKET %hhu \n", TOS_NODE_ID, recv_msg->msg_id);

			dbg("recv", "\t The payload of the packet is: %s \n", recv_msg->payload);

			if(!timer_pack[recv_msg->msg_id]){
				//Node check is it has already received the packed ID. If not, put TRUE the boolean
				if(!recv_pack[recv_msg->msg_id]){
					recv_pack[recv_msg->msg_id] = TRUE;
					dbg("recv", "\t I've set as TRUE the boolean of packet: %d \n", recv_msg->msg_id);
					dbg("recv", "\t SETTING RANDOM TIMER FOR REFORWARDING... \n");
					//Now the NODE has to send again the packet in broadcast
					temp_id = recv_msg->msg_id;
					//temp_payload = recv_msg->payload;
					memcpy(temp_payload, recv_msg->payload, sizeof(nx_uint8_t)*DIMPAYLOAD);

					//in original version, the node always reforward the packet
					//post broadcastNode();
					//Now it has to define a random timer and then start it

					randomTimer = call Random.rand32() % 5000;
					if(randomTimer < 1000){
					 randomTimer = randomTimer + 1234;
					}


					dbg("recv", "The random timer is %d \n", randomTimer);
					call RandomTimer.startOneShot(randomTimer);
					timer_pack[recv_msg->msg_id] = TRUE;
				}
				else{
					dbg("recv", "\t I've already received the packet with ID: %d \n", recv_msg->msg_id);
				}
			}
			else{
					dbg("recv", "I've received a packet for which the random timer is running \n");
					dbg("recv", "STOPPING THE RANDOM TIMER.... \n");
					temp_id = recv_msg->msg_id;
					call RandomTimer.stop();

			}
		}

		return buf;
	}

	//----------- RANDOM TIMER FIRES ----------
	event void RandomTimer.fired(){
		dbg("timer", "\n");
		dbg("timer", "I'm node %d and my RANDOM timer has expired. \n", TOS_NODE_ID);
		dbg("timer", "Proceeding with a REFORWARDING... \n");
		post broadcastNode();
		timer_pack[temp_id] = FALSE;
	}

	//---------- TASK FOR SENDING BROADCAST PACKET -----------
	task void broadcastSink(){
		my_msg_t* msg=(my_msg_t*)(call RadioPacket.getPayload(&packet, sizeof(my_msg_t)));
		msg->msg_id = counter++;
		//*(msg->payload) = call Random.rand16();
		strcpy(msg->payload, STRINGPAYLOAD);
		dbg("sink", "SENT FROM %d \n", TOS_NODE_ID);
		dbg("sink", "Random INT is %d for Packet ID %d \n", msg->payload, msg->msg_id);

		dbg("sink", "Try to send a BROADCAST PACKET at time %s \n", sim_time_string());
		if(call RadioAMSend.send(AM_BROADCAST_ADDR, &packet, sizeof(my_msg_t)) == SUCCESS){
			dbg("radio_pack", "\t Packet dimension: %hhu \n", sizeof(my_msg_t));
			dbg("radio_pack", "\t Source: %hhu \n", call AMPacket.source(&packet));
			dbg("rasdio_pack", "\t Destination: %hhu \n", call AMPacket.destination(&packet));
			dbg("radio_pack", "\t Packet Type: %hhu \n", call AMPacket.type(&packet));
			//dbg("radio_pack", "\t Message Type: %hhu \n", msg->msg_type);
			dbg("radio_pack", "\t Message ID: %d \n", msg->msg_id);
			dbg("radio_pack", "\t Payload: %s \n", msg->payload);
		}
		
	}

	//---------- TASK FOR FORWARDING BROADCAST PACKET -----------
	task void broadcastNode(){
		my_msg_t* msg=(my_msg_t*)(call RadioPacket.getPayload(&packet, sizeof(my_msg_t)));
		msg->msg_id = temp_id;
		//msg->payload = temp_payload;
		memcpy(msg->payload, temp_payload, sizeof(nx_uint8_t)*DIMPAYLOAD);

		dbg("forw", "\n");
		dbg("forw", "SENT FROM %d \n", TOS_NODE_ID);
		dbg("forw", "I'm node %d. Trying to REFORWARD a BROADCAST PACKET at time %s \n", TOS_NODE_ID, sim_time_string());
		if(call RadioAMSend.send(AM_BROADCAST_ADDR, &packet, sizeof(my_msg_t)) == SUCCESS){
			dbg("radio_pack", "\t Packet dimension: %hhu \n", sizeof(my_msg_t));
			dbg("radio_pack", "\t Source: %hhu \n", call AMPacket.source(&packet));
			dbg("radio_pack", "\t Destination: %hhu \n", call AMPacket.destination(&packet));
			dbg("radio_pack", "\t Packet Type: %hhu \n", call AMPacket.type(&packet));
			//dbg("radio_pack", "\t Message Type: %hhu \n", msg->msg_type);
			dbg("radio_pack", "\t Message ID: %d \n", msg->msg_id);
			dbg("radio_pack", "\t Payload: %s \n", msg->payload);
		}
		
	}

}























