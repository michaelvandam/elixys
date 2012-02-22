package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;

	import flash.utils.flash_proxy;
	
	public class PressureRegulatorState extends JSONObject
	{
		// Constructor
		public function PressureRegulatorState(data:String, existingcontent:Object = null)
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
			return "pressureregulatorstate";
		}

		// Data wrappers
		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function get Pressure():Number
		{
			return super.flash_proxy::getProperty("pressure");
		}
	}
}
