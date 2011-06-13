package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ReactorState extends JSONObject
	{
		// Constructor
		public function ReactorState(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type() != null) && (Type() != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Data wrappers
		public function Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function Number():uint
		{
			return parseInt(super.flash_proxy::getProperty("number"));
		}
		public function SetTemperature():String
		{
			return super.flash_proxy::getProperty("settemperature");
		}
		public function ActualTemperature():String
		{
			return super.flash_proxy::getProperty("actualtemperature");
		}
		public function Position():uint
		{
			return parseInt(super.flash_proxy::getProperty("position"));
		}
		public function Vial():String
		{
			return super.flash_proxy::getProperty("vial");
		}
		public function Activity():String
		{
			return super.flash_proxy::getProperty("activity");
		}
		public function ActivityTime():String
		{
			return super.flash_proxy::getProperty("activitytime");
		}
		public function StirSpeed():uint
		{
			return parseInt(super.flash_proxy::getProperty("stirspeed"));
		}
		public function Video():String
		{
			return super.flash_proxy::getProperty("video");
		}
		public function EvaporationValue():String
		{
			return super.flash_proxy::getProperty("evaporationvalves");
		}
		public function TransferValve():String
		{
			return super.flash_proxy::getProperty("transfervalve");
		}
		public function Reagent1TransferValve():String
		{
			return super.flash_proxy::getProperty("reagent1transfervalve");
		}
		public function Reagent2TransferValve():String
		{
			return super.flash_proxy::getProperty("reagent2transfervalve");
		}
		public function Stopcock1Valve():String
		{
			return super.flash_proxy::getProperty("stopcock1valve");
		}
		public function Stopcock2Valve():String
		{
			return super.flash_proxy::getProperty("stopcock2valve");
		}
		public function Stopcock3Valve():String
		{
			return super.flash_proxy::getProperty("stopcock3valve");
		}
		
		// Type
		static public var TYPE:String = "reactorstate";
	}
}
