package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;

	import flash.utils.flash_proxy;
	
	public class VacuumState extends JSONObject
	{
		// Constructor
		public function VacuumState(data:String, existingcontent:Object = null)
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
			return "vacuumstate";
		}

		// Data wrappers
		public function get On():Boolean
		{
			return super.flash_proxy::getProperty("on");
		}
		public function get Vacuum():Number
		{
			return super.flash_proxy::getProperty("vacuum");
		}
	}
}
