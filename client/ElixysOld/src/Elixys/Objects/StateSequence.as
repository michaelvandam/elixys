package Elixys.Objects
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
			if ((ClientState() != null) && (ClientState().Screen() != m_sType))
			{
				throw new Error("State object mismatch");
			}
		}
		
		// Types
		static public var VIEWTYPE:String = "VIEW";
		static public var EDITTYPE:String = "EDIT";
		static public var RUNTYPE:String = "RUN";
		
		// State components
		protected var m_sType:String;
	}
}
