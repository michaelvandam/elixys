package Elixys.JSON.State
{
	import flash.utils.flash_proxy;
	
	public class StateSequence extends State
	{
		// Constructor
		public function StateSequence(sType:String, data:String, existingcontent:Object = null)
		{
			// Remember our type
			m_sType = sType;
			
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((ClientState != null) && !CheckState(ClientState.Screen))
			{
				throw new Error("State object mismatch");
			}
		}

		// Checks for a state match
		static public function CheckState(sState:String):Boolean
		{
			return ((sState == VIEWTYPE) || (sState == EDITTYPE) || (sState == RUNTYPE));
		}

		// Types
		static public var VIEWTYPE:String = "VIEW";
		static public var EDITTYPE:String = "EDIT";
		static public var RUNTYPE:String = "RUN";
		
		// State components
		protected var m_sType:String;
	}
}
