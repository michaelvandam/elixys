package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;

	import flash.utils.flash_proxy;
	
	public class ValveState extends JSONObject
	{
		// Constructor
		public function ValveState(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Static type
		public static function get TYPE():String
		{
			return "valvestate";
		}

		// Data wrappers
		public function get GasTransferValve():Boolean
		{
			return super.flash_proxy::getProperty("gastransfervalve");
		}
		public function get F18LoadValve():Boolean
		{
			return super.flash_proxy::getProperty("f18loadvalve");
		}
		public function get HPLCValve():String
		{
			return super.flash_proxy::getProperty("hplcvalve");
		}
	}
}
