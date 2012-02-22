package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;

	import flash.utils.flash_proxy;
	
	public class LiquidSensorState extends JSONObject
	{
		// Constructor
		public function LiquidSensorState(data:String, existingcontent:Object = null)
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
			return "liquidsensorstate";
		}

		// Data wrappers
		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function get LiquidPresent():Boolean
		{
			return super.flash_proxy::getProperty("liquidpresent");
		}
	}
}
