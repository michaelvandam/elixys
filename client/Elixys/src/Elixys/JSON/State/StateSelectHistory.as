package Elixys.JSON.State
{
	import flash.utils.flash_proxy;
	
	public class StateSelectHistory extends State
	{
		// Constructor
		public function StateSelectHistory(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((ClientState != null) && (ClientState.Screen != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}
		
		// Static type
		public static function get TYPE():String
		{
			return "SELECT_RUNHISTORY";
		}
	}
}
