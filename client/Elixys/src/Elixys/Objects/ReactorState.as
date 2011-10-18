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
		public function ReactorNumber():uint
		{
			return super.flash_proxy::getProperty("number");
		}
		public function Temperature():Number
		{
			return super.flash_proxy::getProperty("temperature");
		}
		public function Position():ReactorPosition
		{
			// Parse the reactor position
			if (m_pReactorPosition == null)
			{
				m_pReactorPosition = new ReactorPosition(null, super.flash_proxy::getProperty("position"));
			}
			return m_pReactorPosition;
		}
		public function Activity():Number
		{
			return super.flash_proxy::getProperty("activity");
		}
		public function ActivityTime():String
		{
			return super.flash_proxy::getProperty("activitytime");
		}
		public function Evaporation():Boolean
		{
			return super.flash_proxy::getProperty("evaporation");
		}
		public function Transfer():Boolean
		{
			return super.flash_proxy::getProperty("transfer");
		}
		public function TransferPosition():String
		{
			return super.flash_proxy::getProperty("transferposition");
		}
		public function Reagent1Transfer():Boolean
		{
			return super.flash_proxy::getProperty("reagent1transfer");
		}
		public function Reagent2Transfer():Boolean
		{
			return super.flash_proxy::getProperty("reagent2transfer");
		}
		public function StirSpeed():uint
		{
			return super.flash_proxy::getProperty("stirspeed");
		}
		public function Video():String
		{
			return super.flash_proxy::getProperty("video");
		}
		public function ColumnPosition():String
		{
			return super.flash_proxy::getProperty("columnposition");
		}
		public function F18Transfer():Boolean
		{
			return super.flash_proxy::getProperty("f18transfer");
		}
		public function EluentTransfer():Boolean
		{
			return super.flash_proxy::getProperty("eluenttransfer");
		}
		
		// Type
		static public var TYPE:String = "reactorstate";
		
		// State components
		private var m_pReactorPosition:ReactorPosition = null;
	}
}
