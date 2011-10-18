package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class StateManualRun extends StateSequence
	{
		// Constructor
		public function StateManualRun(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(StateSequence.MANUALRUNTYPE, data, existingcontent);
			
			// Validate the object type
			if ((ClientState() != null) && (m_sType != ClientState().Screen()))
			{
				throw new Error("State object mismatch");
			}
		}
		
		// Data wrappers
		public function ManualRunStep():String
		{
			return super.flash_proxy::getProperty("manualrunstep");
		}
		public function OperationResult():Boolean
		{
			return super.flash_proxy::getProperty("operationresult");
		}
	}
}
